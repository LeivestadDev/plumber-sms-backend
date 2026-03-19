export interface Customer {
  id: number;
  company_name: string;
  twilio_number: string;
  plumber_phone: string;
  calendly_url: string;
  greeting_message: string | null;
  sms_provider: "twilio" | "46elks";
  is_active: boolean;
  created_at: string;
}

export interface CustomerStats {
  total_conversations: number;
  conversations_last_7_days: number;
  urgent_alerts_sent: number;
}

export interface CustomerWithStats extends Customer {
  stats: CustomerStats;
}

export interface CustomerPatch {
  company_name?: string;
  twilio_number?: string;
  plumber_phone?: string;
  calendly_url?: string;
  greeting_message?: string | null;
  is_active?: boolean;
  sms_provider?: "twilio" | "46elks";
}

export interface Conversation {
  id: number;
  customer_id: number;
  caller_phone: string;
  current_step: string;
  problem_description: string | null;
  address: string | null;
  urgency: string | null;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  direction: "inbound" | "outbound";
  body: string;
  created_at: string;
}

export type ConversationStatus = "active" | "done" | "expired";
