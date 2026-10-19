import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import { GuestOnly, Protected } from "./components/layout/Guards";
import { useAuth } from "./store/auth";
import { useTheme } from "./store/theme";
import { LoginPage } from "./pages/auth/LoginPage";
import { RegisterPage } from "./pages/auth/RegisterPage";
import { InvitePage } from "./pages/auth/InvitePage";
import { DashboardPage } from "./pages/dashboard/DashboardPage";
import { SuppliersPage } from "./pages/suppliers/SuppliersPage";
import { SupplierDetailPage } from "./pages/suppliers/SupplierDetailPage";
import { PurchaseOrdersPage } from "./pages/procurement/PurchaseOrdersPage";
import { PurchaseOrderDetailPage } from "./pages/procurement/PurchaseOrderDetailPage";
import { RequisitionsPage } from "./pages/procurement/RequisitionsPage";
import { InventoryPage } from "./pages/inventory/InventoryPage";
import { WarehousesPage } from "./pages/inventory/WarehousesPage";
import { ShipmentsPage } from "./pages/logistics/ShipmentsPage";
import { ShipmentDetailPage } from "./pages/logistics/ShipmentDetailPage";
import { CarriersPage } from "./pages/logistics/CarriersPage";
import { PlanningPage } from "./pages/planning/PlanningPage";
import { AlertsPage } from "./pages/alerts/AlertsPage";
import { AnalyticsPage } from "./pages/analytics/AnalyticsPage";
import { ReportsPage } from "./pages/analytics/ReportsPage";
import { SettingsPage } from "./pages/settings/SettingsPage";
import { CatalogPage } from "./pages/master-data/CatalogPage";
import { PricingPage } from "./pages/master-data/PricingPage";
import { TaxationPage } from "./pages/master-data/TaxationPage";
import { UomPage } from "./pages/master-data/UomPage";
import { SpecificationsPage } from "./pages/master-data/SpecificationsPage";
import { SourcingPage } from "./pages/sourcing/SourcingPage";
import { ContractsPage } from "./pages/sourcing/ContractsPage";
import { ApprovedListsPage } from "./pages/sourcing/ApprovedListsPage";
import { SupplierPerformancePage } from "./pages/sourcing/SupplierPerformancePage";
import { VendorPortalPage } from "./pages/sourcing/VendorPortalPage";
import { WarehousingPage } from "./pages/warehouse/WarehousingPage";
import { ReceivingPage } from "./pages/warehouse/ReceivingPage";
import { PickingPage } from "./pages/warehouse/PickingPage";
import { CycleCountsPage } from "./pages/warehouse/CycleCountsPage";
import { TransfersPage } from "./pages/warehouse/TransfersPage";
import { PackingPage } from "./pages/fulfillment/PackingPage";
import { ReturnsPage } from "./pages/fulfillment/ReturnsPage";
import { ShippingPage } from "./pages/fulfillment/ShippingPage";
import { DockSchedulingPage } from "./pages/logistics/DockSchedulingPage";
import { YardPage } from "./pages/logistics/YardPage";
import { FreightPage } from "./pages/logistics/FreightPage";
import { CustomsPage } from "./pages/logistics/CustomsPage";
import { RoutesPage } from "./pages/logistics/RoutesPage";
import { TrackingPage } from "./pages/logistics/TrackingPage";
import { FleetPage } from "./pages/logistics/FleetPage";
import { DemandForecastingPage } from "./pages/planning/DemandForecastingPage";
import { MrpPage } from "./pages/planning/MrpPage";
import { CapacityPage } from "./pages/planning/CapacityPage";
import { SchedulingPage } from "./pages/planning/SchedulingPage";
import { ReplenishmentPage } from "./pages/planning/ReplenishmentPage";
import { ManufacturingPage } from "./pages/manufacturing/ManufacturingPage";
import { BillsOfMaterialsPage } from "./pages/manufacturing/BillsOfMaterialsPage";
import { WorkOrdersPage } from "./pages/manufacturing/WorkOrdersPage";
import { QualityPage } from "./pages/manufacturing/QualityPage";
import { MaintenancePage } from "./pages/manufacturing/MaintenancePage";
import { AccountingPage } from "./pages/finance/AccountingPage";
import { InvoicingPage } from "./pages/finance/InvoicingPage";
import { PaymentsPage } from "./pages/finance/PaymentsPage";
import { BudgetingPage } from "./pages/finance/BudgetingPage";
import { CostingPage } from "./pages/finance/CostingPage";
import { SalesOrdersPage } from "./pages/sales/SalesOrdersPage";
import { CustomersPage } from "./pages/sales/CustomersPage";
import { QuotesPage } from "./pages/sales/QuotesPage";
import { CrmPage } from "./pages/sales/CrmPage";
import { SubscriptionsPage } from "./pages/sales/SubscriptionsPage";
import { PurchaseContractsPage } from "./pages/procurement-ext/PurchaseContractsPage";
import { RfqPage } from "./pages/procurement-ext/RfqPage";
import { ApprovalsPage } from "./pages/procurement-ext/ApprovalsPage";
import { VendorInvoicesPage } from "./pages/finance/VendorInvoicesPage";
import { ExpensesPage } from "./pages/finance/ExpensesPage";
import { EmployeesPage } from "./pages/people/EmployeesPage";
import { AttendancePage } from "./pages/people/AttendancePage";
import { LeavePage } from "./pages/people/LeavePage";
import { PayrollPage } from "./pages/people/PayrollPage";
import { RecruitingPage } from "./pages/people/RecruitingPage";
import { TimesheetsPage } from "./pages/people/TimesheetsPage";
import { ResourcesPage } from "./pages/people/ResourcesPage";
import { TicketsPage } from "./pages/support/TicketsPage";
import { ServiceOrdersPage } from "./pages/support/ServiceOrdersPage";
import { KnowledgeBasePage } from "./pages/support/KnowledgeBasePage";
import { WarrantyPage } from "./pages/support/WarrantyPage";
import { FeedbackPage } from "./pages/support/FeedbackPage";
import { CompliancePage } from "./pages/compliance/CompliancePage";
import { RiskPage } from "./pages/compliance/RiskPage";
import { AuditPage } from "./pages/compliance/AuditPage";
import { SafetyPage } from "./pages/compliance/SafetyPage";
import { DocumentControlPage } from "./pages/compliance/DocumentControlPage";
import { ProjectsPage } from "./pages/projects/ProjectsPage";
import { PortfoliosPage } from "./pages/projects/PortfoliosPage";
import { ProjectExpensesPage } from "./pages/projects/ProjectExpensesPage";
import { ReportingPage } from "./pages/platform/ReportingPage";
import { DashboardsPage } from "./pages/platform/DashboardsPage";
import { WorkflowsPage } from "./pages/platform/WorkflowsPage";
import { IntegrationsPage } from "./pages/platform/IntegrationsPage";
import { PortalsPage } from "./pages/platform/PortalsPage";

const client = new QueryClient({ defaultOptions: { queries: { refetchOnWindowFocus: false, retry: 1 } } });

export default function App() {
  const bootstrap = useAuth((s) => s.bootstrap);
  const hydrate = useTheme((s) => s.hydrate);
  useEffect(() => {
    hydrate();
    bootstrap();
  }, [bootstrap, hydrate]);

  return (
    <QueryClientProvider client={client}>
      <BrowserRouter>
        <Routes>
          <Route element={<GuestOnly />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/invite/:id" element={<InvitePage />} />
          </Route>
          <Route element={<Protected />}>
            <Route element={<AppShell />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/suppliers" element={<SuppliersPage />} />
              <Route path="/suppliers/:id" element={<SupplierDetailPage />} />
              <Route path="/purchase-orders" element={<PurchaseOrdersPage />} />
              <Route path="/purchase-orders/:id" element={<PurchaseOrderDetailPage />} />
              <Route path="/requisitions" element={<RequisitionsPage />} />
              <Route path="/inventory" element={<WarehousesPage />} />
              <Route path="/warehouses" element={<InventoryPage />} />
              <Route path="/shipments" element={<ShipmentsPage />} />
              <Route path="/shipments/:id" element={<ShipmentDetailPage />} />
              <Route path="/carriers" element={<CarriersPage />} />
              <Route path="/planning" element={<PlanningPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/catalog" element={<CatalogPage />} />
              <Route path="/pricing" element={<PricingPage />} />
              <Route path="/taxation" element={<TaxationPage />} />
              <Route path="/uom" element={<UomPage />} />
              <Route path="/specifications" element={<SpecificationsPage />} />
              <Route path="/sourcing" element={<SourcingPage />} />
              <Route path="/contracts" element={<ContractsPage />} />
              <Route path="/approved-lists" element={<ApprovedListsPage />} />
              <Route path="/supplier-performance" element={<SupplierPerformancePage />} />
              <Route path="/vendor-portal" element={<VendorPortalPage />} />
              <Route path="/warehousing" element={<WarehousingPage />} />
              <Route path="/receiving" element={<ReceivingPage />} />
              <Route path="/picking" element={<PickingPage />} />
              <Route path="/cycle-counts" element={<CycleCountsPage />} />
              <Route path="/transfers" element={<TransfersPage />} />
              <Route path="/packing" element={<PackingPage />} />
              <Route path="/returns" element={<ReturnsPage />} />
              <Route path="/shipping" element={<ShippingPage />} />
              <Route path="/dock-schedule" element={<DockSchedulingPage />} />
              <Route path="/yard" element={<YardPage />} />
              <Route path="/freight" element={<FreightPage />} />
              <Route path="/customs" element={<CustomsPage />} />
              <Route path="/routes" element={<RoutesPage />} />
              <Route path="/tracking" element={<TrackingPage />} />
              <Route path="/fleet" element={<FleetPage />} />
              <Route path="/demand-forecasting" element={<DemandForecastingPage />} />
              <Route path="/mrp" element={<MrpPage />} />
              <Route path="/capacity" element={<CapacityPage />} />
              <Route path="/scheduling" element={<SchedulingPage />} />
              <Route path="/replenishment" element={<ReplenishmentPage />} />
              <Route path="/manufacturing" element={<ManufacturingPage />} />
              <Route path="/bills-of-materials" element={<BillsOfMaterialsPage />} />
              <Route path="/work-orders" element={<WorkOrdersPage />} />
              <Route path="/quality" element={<QualityPage />} />
              <Route path="/maintenance" element={<MaintenancePage />} />
              <Route path="/accounting" element={<AccountingPage />} />
              <Route path="/invoicing" element={<InvoicingPage />} />
              <Route path="/payments" element={<PaymentsPage />} />
              <Route path="/budgeting" element={<BudgetingPage />} />
              <Route path="/costing" element={<CostingPage />} />
              <Route path="/sales-orders" element={<SalesOrdersPage />} />
              <Route path="/customers" element={<CustomersPage />} />
              <Route path="/quotes" element={<QuotesPage />} />
              <Route path="/crm" element={<CrmPage />} />
              <Route path="/subscriptions" element={<SubscriptionsPage />} />
              <Route path="/purchase-contracts" element={<PurchaseContractsPage />} />
              <Route path="/rfq" element={<RfqPage />} />
              <Route path="/approvals" element={<ApprovalsPage />} />
              <Route path="/vendor-invoices" element={<VendorInvoicesPage />} />
              <Route path="/expenses" element={<ExpensesPage />} />
              <Route path="/employees" element={<EmployeesPage />} />
              <Route path="/attendance" element={<AttendancePage />} />
              <Route path="/leave" element={<LeavePage />} />
              <Route path="/payroll" element={<PayrollPage />} />
              <Route path="/recruiting" element={<RecruitingPage />} />
              <Route path="/timesheets" element={<TimesheetsPage />} />
              <Route path="/resources" element={<ResourcesPage />} />
              <Route path="/tickets" element={<TicketsPage />} />
              <Route path="/service-orders" element={<ServiceOrdersPage />} />
              <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
              <Route path="/warranty" element={<WarrantyPage />} />
              <Route path="/feedback" element={<FeedbackPage />} />
              <Route path="/compliance" element={<CompliancePage />} />
              <Route path="/risk" element={<RiskPage />} />
              <Route path="/audit" element={<AuditPage />} />
              <Route path="/safety" element={<SafetyPage />} />
              <Route path="/document-control" element={<DocumentControlPage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/portfolios" element={<PortfoliosPage />} />
              <Route path="/project-expenses" element={<ProjectExpensesPage />} />
              <Route path="/reporting" element={<ReportingPage />} />
              <Route path="/dashboards" element={<DashboardsPage />} />
              <Route path="/workflows" element={<WorkflowsPage />} />
              <Route path="/integrations" element={<IntegrationsPage />} />
              <Route path="/portals" element={<PortalsPage />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
