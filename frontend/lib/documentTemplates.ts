/**
 * Document Template Presets
 * Pre-configured document combinations for different roles and use cases
 */

export interface DocumentTemplate {
  id: string;
  name: string;
  description: string;
  icon: string;
  documentIds: string[];
}

export const DOCUMENT_TEMPLATES: DocumentTemplate[] = [
  {
    id: 'developer',
    name: 'Developer / Technical Team',
    description: 'Complete technical documentation for development teams',
    icon: '💻',
    documentIds: [
      'requirements',
      'prd',
      'fsd',
      'tad',
      'api_documentation',
      'database_schema',
      'developer_guide',
      'cicd_doc',
      'test_plan',
      'deployment_plan',
    ],
  },
  {
    id: 'product_manager',
    name: 'Product Manager',
    description: 'Essential documents for product planning and management',
    icon: '📊',
    documentIds: [
      'project_charter',
      'business_model',
      'requirements',
      'feature_roadmap',
      'prd',
      'ui_mockups',
      'user_analytics',
      'kpi_metrics_doc',
      'release_notes',
      'user_feedback_plan',
    ],
  },
  {
    id: 'startup_founder',
    name: 'Startup Founder / CEO',
    description: 'Strategic documents for business planning and fundraising',
    icon: '🚀',
    documentIds: [
      'market_research',
      'business_model',
      'project_charter',
      'stakeholders_doc',
      'gtm_strategy',
      'feature_roadmap',
      'risk_management_plan',
      'kpi_metrics_doc',
    ],
  },
  {
    id: 'designer',
    name: 'UI/UX Designer',
    description: 'Design and user experience documentation',
    icon: '🎨',
    documentIds: [
      'prd',
      'ui_mockups',
      'ui_style_guide',
      'interaction_flows',
      'onboarding_flow',
      'accessibility_plan',
      'localization_plan',
    ],
  },
  {
    id: 'operations',
    name: 'Operations / DevOps',
    description: 'Operations, deployment, and infrastructure documentation',
    icon: '⚙️',
    documentIds: [
      'tad',
      'cicd_doc',
      'deployment_plan',
      'monitoring_logging_plan',
      'backup_recovery_plan',
      'scalability_plan',
      'maintenance_plan',
      'incident_response_plan',
    ],
  },
  {
    id: 'compliance',
    name: 'Compliance / Legal',
    description: 'Legal, security, and compliance documentation',
    icon: '🔒',
    documentIds: [
      'security_plan',
      'privacy_policy',
      'data_retention_policy',
      'terms_of_service',
      'accessibility_plan',
      'technical_audit',
    ],
  },
  {
    id: 'support',
    name: 'Customer Support',
    description: 'User support and knowledge base documentation',
    icon: '🎧',
    documentIds: [
      'user_support_doc',
      'knowledge_base',
      'support_playbook',
      'support_training_doc',
      'user_feedback_plan',
    ],
  },
  {
    id: 'minimal',
    name: 'Minimal / Quick Start',
    description: 'Essential documents for quick project setup',
    icon: '⚡',
    documentIds: [
      'project_charter',
      'requirements',
      'prd',
      'developer_guide',
    ],
  },
  {
    id: 'comprehensive',
    name: 'Comprehensive / Full Suite',
    description: 'Complete documentation suite for enterprise projects',
    icon: '📚',
    documentIds: [
      'market_research',
      'business_model',
      'project_charter',
      'stakeholders_doc',
      'requirements',
      'feature_roadmap',
      'wbs',
      'prd',
      'fsd',
      'tad',
      'ui_mockups',
      'api_documentation',
      'database_schema',
      'test_plan_doc',
      'developer_guide',
      'security_plan',
      'privacy_policy',
      'deployment_plan',
    ],
  },
  {
    id: 'brick_and_mortar',
    name: 'Brick-and-Mortar Business',
    description: 'Complete business documentation for physical businesses (restaurants, retail, services)',
    icon: '🏪',
    documentIds: [
      'business_overview',
      'operations_plan',
      'market_research',
      'financial_model',
      'licensing_checklist',
      'sop',
      'hr_staffing_guide',
      'marketing_plan',
      'risk_management_plan',
      'customer_experience_playbook',
      'growth_expansion_plan',
      'execution_roadmap',
    ],
  },
];

/**
 * Get template by ID
 */
export function getTemplateById(id: string): DocumentTemplate | undefined {
  return DOCUMENT_TEMPLATES.find((t) => t.id === id);
}

/**
 * Get all available templates
 */
export function getAllTemplates(): DocumentTemplate[] {
  return DOCUMENT_TEMPLATES;
}

