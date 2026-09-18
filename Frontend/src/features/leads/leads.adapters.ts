import type {
  LeadDetailResponseApi,
  LeadPrioritizedItemApi,
  LeadScoreDetailApi,
  LeadConversationsResponseApi,
} from './leads.schemas'
import type {
  LeadConversation,
  LeadDetail,
  LeadPriority,
  PrioritizedLead,
  ScoreFactor,
} from './lead.types'

/**
 * Convierte el tier del backend (ALTA, MEDIA, BAJA) al tipo de prioridad UI (high, medium, low).
 */
export function adaptPriorityTier(tier?: string | null): LeadPriority {
  switch (tier?.toUpperCase()) {
    case 'ALTA':
      return 'high'
    case 'MEDIA':
      return 'medium'
    case 'BAJA':
      return 'low'
    default:
      return 'low'
  }
}

/**
 * Normaliza el canal de adquisición al formato canónico (WhatsApp, Meta Ads, Formulario Web).
 */
export function normalizeChannel(channel?: string | null): string | null {
  if (!channel) return null
  const cleaned = channel.trim()
  const lower = cleaned.toLowerCase()
  if (lower.includes('whatsapp')) return 'WhatsApp'
  if (lower.includes('meta') || lower.includes('face') || lower.includes('ads')) return 'Meta Ads'
  if (lower.includes('formulario') || lower.includes('web')) return 'Formulario Web'
  return cleaned
}

/**
 * Adapta un elemento de la lista paginada de FastAPI al modelo PrioritizedLead de la UI.
 */
export function adaptApiLeadToPrioritizedLead(item: LeadPrioritizedItemApi): PrioritizedLead {
  return {
    id: item.lead_id,
    companyId: item.company_id,
    salesPointId: item.sales_point_id,
    customerName: item.customer_name?.trim() || 'Prospecto sin nombre',
    channel: normalizeChannel(item.channel),
    managementStatus: item.management_status ?? null,
    modelInterestText: item.model_interest ?? null,
    registeredAt: item.registered_at ?? null,
    priority: adaptPriorityTier(item.priority_tier),
    score: item.score ?? null,
  }
}

/**
 * Adapta los datos reales de detalle, score y conversaciones en el modelo LeadDetail de la UI.
 */
export function adaptApiLeadDetail(
  detail: LeadDetailResponseApi,
  scoreData?: LeadScoreDetailApi | null,
  conversationsData?: LeadConversationsResponseApi | null
): LeadDetail {
  const scoreFactors: ScoreFactor[] = []

  if (scoreData?.factors) {
    for (const factor of Object.values(scoreData.factors)) {
      const ratio = factor.max_score > 0 ? factor.score_obtained / factor.max_score : 0
      const impact: 'positive' | 'neutral' | 'negative' =
        ratio >= 0.7 ? 'positive' : ratio >= 0.4 ? 'neutral' : 'negative'

      scoreFactors.push({
        label: factor.name,
        description: `${factor.description} (Puntaje: ${factor.score_obtained}/${factor.max_score} - Ponderación: ${factor.weight_pct}%)`,
        impact,
      })
    }
  }

  let scoreExplanation: string | null = null
  if (scoreData) {
    const probPct =
      scoreData.conversion_probability !== null && scoreData.conversion_probability !== undefined
        ? ` con probabilidad calibrada de compra del ${(scoreData.conversion_probability * 100).toFixed(1)}%`
        : ''
    scoreExplanation = `Prospecto con score ${scoreData.score}/100 (${scoreData.priority_tier})${probPct}, evaluado mediante el modelo ${scoreData.model_version}.`
  } else if (detail.score !== null && detail.score !== undefined) {
    scoreExplanation = `Prospecto clasificado con score ${detail.score}. Desglose de factores no disponible en el servicio de scoring.`
  }

  const conversations: LeadConversation[] = (conversationsData?.conversations ?? []).map((c) => ({
    id: c.conversation_id,
    channel: c.channel || 'WhatsApp',
    startedAt: c.started_at || '',
    messages: c.messages.map((m) => ({
      id: `${c.conversation_id}-${m.sequence_number}`,
      sender: m.sender,
      sentAt: m.message_time || '',
      text: m.text,
    })),
  }))

  return {
    id: detail.lead_id,
    companyId: detail.company_id,
    salesPointId: detail.sales_point_id,
    customerName: detail.customer_name?.trim() || 'Prospecto sin nombre',
    channel: normalizeChannel(detail.channel),
    managementStatus: detail.management_status ?? null,
    modelInterestText: detail.model_interest_text ?? null,
    registeredAt: detail.registered_at ?? null,
    priority: adaptPriorityTier(detail.priority_tier),
    score: detail.score ?? null,
    firstContactAt: detail.first_contact_at ?? null,
    campaign: detail.campaign ?? null,
    city: detail.city ?? null,
    scoreExplanation,
    scoreFactors,
    conversations,
  }
}
