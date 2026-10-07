import fallback from '../data/fallback.json'

export type Pocket = typeof fallback.items[number] & {
  shap_reasons?: { feature: string; label: string; contribution: number }[]
  intervention?: { top_options: { type: string; probability: number }[]; reasons: string[] }
  service_assurance?: Record<string, number>
}
export type Summary = typeof fallback.summary
export type FeasibilityInput = {
  land_area_sqm: number; fsi: number; eligible_households: number; rehab_area_sqft: number;
  construction_cost_per_sqft: number; market_sale_rate_per_sqft: number;
  tdr_value_per_sqft: number; premiums_and_fees_pct: number; sales_share_pct: number
}
export type FeasibilityResult = {
  gross_built_up_area_sqft: number; free_rehab_area_sqft: number; saleable_area_sqft: number;
  construction_cost_inr: number; fees_inr: number; tdr_support_inr: number; gross_sales_support_inr: number;
  developer_profit_inr: number; developer_margin_pct: number; indicative_irr_pct: number;
  break_even_market_rate_per_sqft: number; verdict: string
}
export type Complaint = { complaint_id: string; text: string; pocket_id?: string; category: string; urgency: string; confidence: number; expected_resolution_days: number; status: string }
export const API_BASE = 'http://localhost:8000'
export let offline = false

async function request<T>(path: string, fallbackValue: () => T, body?: unknown): Promise<T> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 6000)
  try {
    const response = await fetch(`${API_BASE}${path}`, { method: body ? 'POST' : 'GET', headers: { 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined, signal: controller.signal })
    if (!response.ok) throw new Error(`API ${response.status}`)
    offline = false
    return await response.json() as T
  } catch {
    offline = true
    return fallbackValue()
  } finally { window.clearTimeout(timeout) }
}

export const getPockets = () => request<{ items: Pocket[]; total: number }>('/pockets', () => ({ items: fallback.items, total: 1500 }))
export const getSummary = () => request<Summary>('/stats/summary', () => fallback.summary)
export const getPocket = (id: string) => request<Pocket>(`/pockets/${id}`, () => fallback.items.find(p => p.pocket_id === id) || fallback.items[0])

export function localFeasibility(p: FeasibilityInput): FeasibilityResult {
  const gross = p.land_area_sqm * 10.7639 * p.fsi
  const rehab = p.eligible_households * p.rehab_area_sqft
  const sale = Math.max(gross - rehab, 0)
  const cost = gross * p.construction_cost_per_sqft
  const fees = cost * p.premiums_and_fees_pct
  const tdr = gross * p.tdr_value_per_sqft
  const revenue = sale * p.market_sale_rate_per_sqft * p.sales_share_pct
  const profit = revenue + tdr - cost - fees
  const irr = (Math.max(revenue + tdr, 1) / Math.max(cost + fees, 1)) ** (1 / 3) - 1
  return { gross_built_up_area_sqft: gross, free_rehab_area_sqft: rehab, saleable_area_sqft: sale, construction_cost_inr: cost, fees_inr: fees, tdr_support_inr: tdr, gross_sales_support_inr: revenue, developer_profit_inr: profit, developer_margin_pct: profit / Math.max(revenue + tdr, 1) * 100, indicative_irr_pct: irr * 100, break_even_market_rate_per_sqft: Math.max(cost + fees - tdr, 0) / Math.max(sale * p.sales_share_pct, 1), verdict: profit > 0 && irr >= .08 ? 'Viable' : profit >= -cost * .1 ? 'Borderline' : 'Not viable' }
}
export const simulate = (p: FeasibilityInput) => request<{ result: FeasibilityResult; sensitivity: { factor: string; profit_inr: number; margin_pct: number; verdict: string }[] }>('/feasibility/simulate', () => ({ result: localFeasibility(p), sensitivity: [] }), p)

export type Optimisation = { solver: string; spent_inr: number; impact_people: number; vulnerable_share: number; selected: { pocket_id: string; city: string; ward: string; priority_score: number; cost_inr: number; impact: number }[]; pareto: { budget_inr: number; impact_people: number }[] }
export const optimise = (budget: number, vulnerable: number, wards: number, pockets: Pocket[]) => request<Optimisation>('/optimize', () => {
  let spent = 0
  const selected = pockets.sort((a, b) => b.priority_score - a.priority_score).filter(p => { const cost = p.population * 12000; if (spent + cost > budget) return false; spent += cost; return true }).map(p => ({ ...p, cost_inr: p.population * 12000, impact: Math.round(p.population * p.priority_score / 100) }))
  const impact = selected.reduce((sum, p) => sum + p.impact, 0)
  return { solver: 'Offline demo plan', spent_inr: spent, impact_people: impact, vulnerable_share: selected.length ? selected.filter(p => p.priority_score >= 65).length / selected.length : 0, selected, pareto: [.2, .4, .6, .8, 1].map(f => ({ budget_inr: budget * f, impact_people: Math.round(impact * f ** .8) })) }
}, { budget_inr: budget, min_vulnerable_share: vulnerable, min_wards: wards })

export type Eligibility = { eligible_schemes: string[]; reasons: string[]; documents_required: string[]; next_steps: string[]; disclaimer: string }
export const checkEligibility = (inputs: Record<string, unknown>) => request<Eligibility>('/eligibility/check', () => ({ eligible_schemes: Number(inputs.monthly_income_inr) < 25000 ? ['Affordable rental housing', ...(inputs.has_aadhaar ? ['PMAY-U screening'] : []), ...(inputs.tenure_document ? ['SRA screening'] : [])] : ['Ward help desk verification'], reasons: ['Income and document information meet the demo screening rules.'], documents_required: ['Identity proof', 'Income proof', 'Address / residence proof', 'Bank account details'], next_steps: ['Visit your ward help desk', 'Request a field verification'], disclaimer: 'Screening only. Final eligibility is decided by the relevant authority.' }), inputs)

const stored = () => JSON.parse(localStorage.getItem('nagarseva-complaints') || '[]') as Complaint[]
export const classify = (text: string, language: string) => request<Omit<Complaint, 'complaint_id' | 'text' | 'status'>>('/grievance/classify', () => {
  const terms: Record<string, string[]> = { water: ['water', 'paani', 'पानी', 'पाणी'], sanitation: ['toilet', 'शौचालय'], power: ['power', 'light', 'bijli', 'बिजली'], waste: ['garbage', 'kachra', 'कचरा'], drainage: ['drain', 'nala', 'नाला'], health: ['fever', 'clinic'], safety: ['unsafe', 'fire'], housing: ['sra', 'housing'] }
  const category = Object.keys(terms).find(key => terms[key].some(term => text.toLowerCase().includes(term))) || 'housing'
  const urgency = /fire|unsafe|fever|danger|गंदा/.test(text.toLowerCase()) ? 'urgent' : 'standard'
  return { category, urgency, confidence: .78, expected_resolution_days: urgency === 'urgent' ? 2 : 7 }
}, { text, language })
export const submitComplaint = async (text: string, language: string, pocket_id: string) => {
  const result = await classify(text, language)
  return request<Complaint>('/grievances', () => {
    const item = { ...result, complaint_id: `DEMO-${Date.now().toString().slice(-6)}`, text, pocket_id, status: 'received' }
    localStorage.setItem('nagarseva-complaints', JSON.stringify([item, ...stored()]))
    return item
  }, { text, language, pocket_id })
}
export const getComplaints = () => request<{ items: Complaint[]; total: number }>('/grievances', () => ({ items: stored(), total: stored().length }))
export const money = (n: number) => Math.abs(n) >= 1e7 ? `₹${(n / 1e7).toFixed(1)} Cr` : `₹${(n / 1e5).toFixed(1)} L`
export const number = (n: number) => Math.round(n).toLocaleString('en-IN')
