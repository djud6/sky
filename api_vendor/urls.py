from django.urls import path
from .Views.Test import TestView
from .Views.Ratings import RatingsView
from .Views.AssetRequest import AssetRequestView
from .Views.Disposal import DisposalView
from .Views.Maintenance import MaintenanceView
from .Views.Repairs import RepairsView
from .Views.Vendors import VendorsView
from .Views.RequestQuote import RequestQuoteView
from .Views.Transfers import TransferView

urlpatterns = [
    path("TestConnectionFromVendor", TestView.TestConnectionFromVendorServer.as_view()),
    path("TestVendorRouting/<str:client_name>", TestView.TestVendorRouting.as_view()),
    path("TestClientRouting", TestView.TestClientRouting.as_view()),
    path("Repair/Get/<str:client_name>", RepairsView.GetRepairRequests.as_view()),
    path("Repair/Get/Details/<str:client_name>", RepairsView.GetRepairRequestDetails.as_view()),
    path("Repair/Update/<str:client_name>", RepairsView.UpdateRepairStatus.as_view()),
    path("Repair/Upload/Files/<str:client_name>", RepairsView.UploadRepairFiles.as_view()),
    path("Disposal/Get/<str:client_name>", DisposalView.GetDisposalRequests.as_view()),
    path("Disposal/Get/Details/<str:client_name>", DisposalView.GetDisposalRequestDetails.as_view()),
    path("Disposal/Update/<str:client_name>", DisposalView.UpdateDisposalStatus.as_view()),
    path("Disposal/Upload/Files/<str:client_name>", DisposalView.UploadDisposalFiles.as_view()),
    path("Maintenance/Get/<str:client_name>", MaintenanceView.GetMaintenanceRequests.as_view()),
    path("Maintenance/Get/Details/<str:client_name>", MaintenanceView.GetMaintenanceRequestDetails.as_view()),
    path("Maintenance/Update/<str:client_name>", MaintenanceView.UpdateMaintenanceStatus.as_view()),
    path("Maintenance/Upload/Files/<str:client_name>", MaintenanceView.UploadMaintenancesFiles.as_view()),
    path("AssetRequest/Get/<str:client_name>", AssetRequestView.GetAssetRequests.as_view()),
    path("AssetRequest/Get/Details/<str:client_name>", AssetRequestView.GetAssetRequestDetails.as_view()),
    path("AssetRequest/Update/<str:client_name>", AssetRequestView.UpdateAssetRequestStatus.as_view()),
    path("AssetRequest/Upload/Files/<str:client_name>", AssetRequestView.UploadAssetRequestFiles.as_view()),
    path("Ratings/Add", RatingsView.AddRating.as_view()),
    path("Vendors/Update/Ratings", VendorsView.UpdateVendorRatingsForAllClients.as_view()),
    path('Vendors/Connection/Request/Add/<str:vendor_name>', VendorsView.AddClientConnectionRequest.as_view()),
    path('Vendors/Add/<str:client_name>', VendorsView.AddApprovedVendor.as_view()),
    path('Vendors/Get/All', VendorsView.ListAllAvailableVendor.as_view()),
    path('Vendors/Update/Services', VendorsView.UpdateVendorServices.as_view()),
    path("Request/Quote/Update/<str:client_name>", RequestQuoteView.UpdateQuote.as_view()),
    path('Request/Quote/Approve/<str:request_quote_id>', RequestQuoteView.ApproveQuote.as_view()),
    path("Transfer/Get/<str:client_name>", TransferView.GetTransferRequests.as_view()),
    path("Transfer/Get/Details/<str:client_name>", TransferView.GetTransferRequestDetails.as_view()),
    path("Transfer/Upload/Files/<str:client_name>", TransferView.UploadTransferFiles.as_view()),
    path("Transfer/Update/<str:client_name>", TransferView.UpdateTransferStatus.as_view()),
    path('AssetRequest/Quote/Reject/<str:asset_request_id>', RequestQuoteView.RejectAssetQuote.as_view()),
    path('Maintenance/Quote/Reject/<str:maintenance_request_id>', RequestQuoteView.RejectMaintenanceQuote.as_view()),
    path('Disposal/Quote/Reject/<str:disposal_request_id>', RequestQuoteView.RejectDisposalQuote.as_view()),
    path('Repair/Quote/Reject/<str:repair_request_id>', RequestQuoteView.RejectRepairQuote.as_view()),
    path('Transfer/Quote/Reject/<str:transfer_request_id>', RequestQuoteView.RejectTransferQuote.as_view()),
    path('Quotes/Reject', RequestQuoteView.RejectQuotes.as_view()),
]
