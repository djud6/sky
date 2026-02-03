import { lazy } from "react";

import "../../styles/navigationSidebar.scss";
import "../../styles/navigationSidebar.scss";
import fleet from "../../images/menu/icon_menu_dashboard.png";
import transfers from "../../images/menu/icon_menu_transfers.png";
import repairs from "../../images/menu/icon_menu_repairs.png";
import maintenance from "../../images/menu/icon_menu_maintenance.png";
import incidents from "../../images/menu/icon_menu_incidents.png";
import issues from "../../images/menu/icon_menu_issues.png";
import operators from "../../images/menu/icon_menu_operators.png";
import removal from "../../images/menu/icon_menu_disposal.png";
import assetReq from "../../images/menu/icon_menu_assets.png";
import energy from "../../images/menu/icon_menu_energy.png";
import inventory from "../../images/menu/icon_menu_inventory.png";

const FleetPanel = lazy(() => import("../../components/FleetPanel/Dashboard"));
const OperatorHomepage = lazy(() => import("../../components/FleetPanel/Dashboard/OperatorPanel"));
const FleetOverviewPanel = lazy(() => import("../../components/Assets/FleetOverview"));
const AssetRequestPanel = lazy(() => import("../../components/Assets/AssetRequest"));
const AssetCurrentOrdersPanel = lazy(() => import("../../components/Assets/CurrentOrders"));
const TransfersPanel = lazy(() => import("../../components/TransfersPanel/AssetTransferMap"));
const ListTransfersPanel = lazy(() => import("../../components/TransfersPanel/ListTransfers"));
const AssetTransferPanel = lazy(() => import("../../components/TransfersPanel/TransferAsset"));
const RepairsPanel = lazy(() => import("../../components/RepairsPanel/ListRepairs"));
const RepairRequestPanel = lazy(() => import("../../components/RepairsPanel/RepairRequest"));
const MaintenancePanel = lazy(() => import("../../components/MaintenancePanel/MaintenanceStatus"));
const ScheduleMaintenancePanel = lazy(() =>
  import("../../components/MaintenancePanel/ScheduleMaintenance")
);
const MaintenanceForecastPanel = lazy(() =>
  import("../../components/MaintenancePanel/MaintenanceForecast")
);
const MaintenanceLookupPanel = lazy(() =>
  import("../../components/MaintenancePanel/MaintenanceLookup")
);
const IncidentReportsPanel = lazy(() => import("../../components/IncidentsPanel/IncidentReports"));
const ReportIncidentPanel = lazy(() => import("../../components/IncidentsPanel/ReportNewIncident"));
const IssuesPanel = lazy(() => import("../../components/IssuesPanel/UnresolvedIssues"));
const SearchIssuesPanel = lazy(() => import("../../components/IssuesPanel/SearchIssues"));
const ReportIssuePanel = lazy(() => import("../../components/IssuesPanel/ReportNewIssue"));
const DailyOperatorsCheckPanel = lazy(() =>
  import("../../components/OperatorsPanel/DailyOperatorsCheck")
);
const UnfinishedChecksPanel = lazy(() =>
  import("../../components/OperatorsPanel/UnfinishedChecks")
);
const LookupDailyChecksPanel = lazy(() =>
  import("../../components/OperatorsPanel/LookupDailyChecks")
);
const EnergyPanel = lazy(() => import("../../components/EnergyPanel/FuelTracking"));
const FuelTransactionPanel = lazy(() => import("../../components/EnergyPanel/FuelTransaction"));
const FuelOrdersHistoryPanel = lazy(() => import("../../components/EnergyPanel/FuelOrdersHistory"));
const FuelCardsPanel = lazy(() => import("../../components/EnergyPanel/FuelCards"));
const RemovalPanel = lazy(() => import("../../components/DisposalPanel/AssetDisposal"));
const RemovalHistory = lazy(() => import("../../components/DisposalPanel/RemovalHistory"));
const ManageInventoryPanel = lazy(() => import("../../components/InventoryPanel/ManageInventory"));

/* Navigation items in JSON format */
const NavigationItems = [
  {
    label: "navigationItems.dashboard",
    image: fleet,
    to: "/dashboard",
    exact: true,
    module: "dashboard", // give the lowest permission, will check the tab permission on the fleetpanel page
    content: FleetPanel,
    items: [
      {
        label: "navigationItems.fleet_at_a_glance",
        image: fleet,
        to: "/dashboard",
        exact: true,
        module: "fleet_at_a_glance",
        content: FleetPanel,
      },
      {
        label: "navigationItems.homepage",
        image: fleet,
        to: "/dashboard",
        exact: true,
        module: "dashboard_operator",
        content: OperatorHomepage,
      },
    ],
  },
  { separator: true },
  {
    label: "navigationItems.assets",
    image: assetReq,
    to: "/assets",
    exact: true,
    module: "asset_request",
    items: [
      {
        label: "navigationItems.fleet_overview",
        image: fleet,
        to: "/assets-overview",
        exact: true,
        module: "fleet_overview",
        content: FleetOverviewPanel,
      },
      {
        label: "navigationItems.asset_request",
        image: assetReq,
        to: "/assets/asset-request",
        exact: true,
        module: "asset_request_new_order",
        content: AssetRequestPanel,
      },
      {
        label: "navigationItems.current_orders",
        image: fleet,
        to: "/assets/current-order",
        exact: true,
        module: "asset_request_list",
        content: AssetCurrentOrdersPanel,
      },
    ],
  },
  { separator: true },
  {
    label: "navigationItems.transfers",
    image: transfers,
    to: "/transfers",
    exact: true,
    module: "asset_transfers",
    badgeKey: "transfers",
    items: [
      {
        label: "navigationItems.asset_transfers_map",
        to: "/transfers",
        image: transfers,
        badgeKey: "transfers",
        exact: true,
        module: "asset_transfers_map",
        content: TransfersPanel,
      },
      {
        label: "navigationItems.list_transfers",
        to: "/transfers/list",
        image: transfers,
        badgeKey: "transfers",
        exact: true,
        module: "asset_transfers_current_transfers",
        content: ListTransfersPanel,
      },
      {
        label: "navigationItems.asset_transfer",
        to: "/transfers/asset-transfer",
        image: transfers,
        badgeKey: "transfers",
        exact: true,
        module: "asset_transfers_new_transfer_request",
        content: AssetTransferPanel,
      },
    ],
  },
  { separator: true },
  {
    label: "navigationItems.issues",
    image: issues,
    module: "issues",
    to: "/issues",
    exact: true,
    badgeKey: "issues",
    items: [
      {
        label: "navigationItems.unresolved_issues",
        image: issues,
        badgeKey: "issues",
        to: "/issues",
        exact: true,
        module: "issues_list",
        content: IssuesPanel,
      },
      {
        label: "navigationItems.search_issues",
        image: fleet,
        to: "/issues/search",
        module: "issues_search",
        exact: true,
        content: SearchIssuesPanel,
      },
      {
        label: "navigationItems.report_new_issue",
        image: fleet,
        to: "/issues/new",
        module: "issues_new",
        exact: false,
        content: ReportIssuePanel,
      },
    ],
  },
  { separator: true },
  {
    label: "navigationItems.repairs",
    image: repairs,
    to: "/repairs",
    exact: true,
    module: "repairs",
    badgeKey: "repairs",
    items: [
      {
        label: "navigationItems.list_repairs",
        to: "/repairs",
        image: repairs,
        badgeKey: "repairs",
        exact: true,
        module: "repairs_list",
        content: RepairsPanel,
      },
      {
        label: "navigationItems.repair_request",
        image: fleet,
        to: "/repairs/request",
        exact: false,
        module: "repairs_new_request",
        content: RepairRequestPanel,
      },
    ],
  },
  { separator: true },
  {
    label: "navigationItems.maintenance",
    to: "/maintenance",
    image: maintenance,
    exact: true,
    badgeKey: "maintenances",
    module: "maintenance",
    items: [
      {
        label: "navigationItems.maintenance_status",
        image: maintenance,
        badgeKey: "maintenances",
        to: "/maintenance",
        exact: true,
        module: "maintenance_status",
        content: MaintenancePanel,
      },
      {
        label: "navigationItems.schedule_maintenance",
        image: fleet,
        to: "/maintenance/schedule",
        exact: false,
        module: "maintenance_new_request",
        content: ScheduleMaintenancePanel,
      },
      {
        label: "navigationItems.maintenance_forecast",
        image: fleet,
        to: "/maintenance/forecast",
        exact: true,
        tooltip: "See your forecasted maintenance and setup forecast rules",
        module: "maintenance_forecast",
        content: MaintenanceForecastPanel,
      },
      {
        label: "navigationItems.maintenance_lookup",
        image: fleet,
        to: "/maintenance/lookup",
        exact: true,
        tooltip: "test",
        module: "maintenance_lookup",
        content: MaintenanceLookupPanel,
      },
    ],
  },
  { separator: true },
  {
    label: "navigationItems.incidents",
    image: incidents,
    module: "incidents",
    to: "/incidents",
    exact: true,
    badgeKey: "incidents",
    items: [
      {
        label: "navigationItems.incident_reports",
        image: incidents,
        to: "/incidents",
        badgeKey: "incidents",
        exact: true,
        module: "incidents_list",
        content: IncidentReportsPanel,
      },
      {
        label: "navigationItems.report_new_incident",
        image: fleet,
        to: "/incidents/new",
        exact: false,
        module: "incidents_new_report",
        content: ReportIncidentPanel,
      },
    ],
  },
  { separator: true },
  {
    label: "navigationItems.operators",
    image: operators,
    module: "operators",
    to: "/operators",
    exact: true,
    badgeKey: "opChecks",
    items: [
      {
        label: "navigationItems.daily_operators_check",
        image: operators,
        to: "/operators",
        module: "operators_daily_check",
        exact: true,
        content: DailyOperatorsCheckPanel,
      },
      {
        label: "navigationItems.unfinished_checks",
        image: operators,
        to: "/operators/unfinished-checks",
        module: "unfinished_checks",
        exact: true,
        content: UnfinishedChecksPanel,
      },
      {
        label: "navigationItems.lookup_daily_checks",
        image: fleet,
        to: "/operators/lookup",
        module: "operators_search",
        exact: true,
        content: LookupDailyChecksPanel,
      },
    ],
  },
  { separator: true },
  {
    label: "navigationItems.energy",
    image: energy,
    to: "/energy",
    module: "energy",
    exact: true,
    items: [
      {
        label: "navigationItems.fuel_tracking",
        image: energy,
        to: "/energy",
        exact: true,
        module: "energy_fuel_tracking",
        content: EnergyPanel,
      },
      {
        label: "navigationItems.fuel_transaction",
        image: energy,
        to: "/energy/fuel-transaction",
        exact: true,
        module: "fuel_transactions",
        content: FuelTransactionPanel,
      },
      {
        label: "navigationItems.fuel_orders",
        image: energy,
        to: "/energy/energy-orders",
        exact: true,
        module: "fuel_orders",
        content: FuelOrdersHistoryPanel,
      },
      {
        label: "navigationItems.fuel_cards",
        image: energy,
        to: "/energy/fuel-cards",
        exact: true,
        module: "fuel_orders",
        content: FuelCardsPanel,
      },
    ],
  },
  { separator: true },
  {
    label: "navigationItems.asset_removal",
    to: "/asset-removal",
    image: removal,
    exact: true,
    module: "asset_removal",
    badgeKey: "removals",
    items: [
      {
        label: "navigationItems.asset_removal_request",
        image: removal,
        badgeKey: "removals",
        to: "/asset-removal",
        exact: true,
        module: "asset_removal_new",
        content: RemovalPanel,
      },
      {
        label: "navigationItems.removal_history",
        image: fleet,
        to: "/asset-removal/history",
        exact: true,
        module: "asset_removal_list",
        content: RemovalHistory,
      },
    ],
  },
  { separator: true },
  {
    label: "navigationItems.inventory",
    to: "/inventory",
    image: inventory,
    exact: true,
    module: "inventory",
    items: [
      {
        label: "navigationItems.inventory_manage",
        image: inventory,
        to: "/inventory",
        exact: true,
        module: "inventory_manage",
        content: ManageInventoryPanel,
      },
    ],
  },
  // { separator: true },
  // {
  //   label: "navigationItems.example",
  //   image: fleet,
  //   to: "/example",
  //   exact: true,
  //   module: "fleet_at_a_glance",
  //   content: ExamplePanel,
  //   items: [
  //     {
  //       label: "navigationItems.example",
  //       image: fleet,
  //       to: "/example",
  //       exact: true,
  //       module: "fleet_at_a_glance",
  //       content: ExamplePanel,
  //     },
  //   ],
  // },
];

export default NavigationItems;
