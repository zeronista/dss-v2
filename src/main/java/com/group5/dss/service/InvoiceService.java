package com.group5.dss.service;

import com.group5.dss.model.Invoice;
import com.group5.dss.util.LocalDataLoader;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class InvoiceService {
    
    @Autowired
    private LocalDataLoader localDataLoader;
    
    /**
     * Get all invoices with pagination from FULL LOCAL CSV
     * Using FULL dataset including cancelled orders for Admin role
     */
    public Page<Invoice> getAllInvoices(int page, int size) {
        System.out.println("📋 Loading invoices from FULL LOCAL CSV (including cancelled orders)...");
        
        // Load all invoices from local CSV (FULL dataset)
        List<Invoice> allInvoices = localDataLoader.loadFullTransactions();
        
        // Implement pagination manually
        int totalElements = allInvoices.size();
        int startIndex = page * size;
        int endIndex = Math.min(startIndex + size, totalElements);
        
        // Get invoices for current page
        List<Invoice> pageContent = (startIndex < totalElements) 
            ? new ArrayList<>(allInvoices.subList(startIndex, endIndex))
            : new ArrayList<>();
        
        // Create Page object
        Pageable pageable = PageRequest.of(page, size);
        Page<Invoice> invoicePage = new PageImpl<>(pageContent, pageable, totalElements);
        
        System.out.println("✅ Loaded page " + (page + 1) + " with " + pageContent.size() + " invoices (Total: " + totalElements + ")");
        
        return invoicePage;
    }
    
    /**
     * Get total count of invoices from FULL LOCAL CSV
     */
    public long getTotalCount() {
        List<Invoice> allInvoices = localDataLoader.loadFullTransactions();
        return allInvoices.size();
    }
    
    /**
     * Search invoices with filters and pagination
     */
    public Page<Invoice> searchInvoices(
            String invoiceNo, 
            String stockCode, 
            String description, 
            String customerId, 
            String country,
            int page, 
            int size) {
        
        System.out.println("🔍 Searching invoices with filters...");
        
        // Load all invoices from local CSV
        List<Invoice> allInvoices = localDataLoader.loadFullTransactions();
        
        // Apply filters
        List<Invoice> filteredInvoices = new ArrayList<>();
        for (Invoice invoice : allInvoices) {
            boolean matches = true;
            
            // Filter by Invoice No (exact match or contains)
            if (invoiceNo != null && !invoiceNo.trim().isEmpty()) {
                String searchInvoiceNo = invoiceNo.trim().toUpperCase();
                String invoiceInvoiceNo = invoice.getInvoiceNo() != null ? String.valueOf(invoice.getInvoiceNo()) : "";
                matches = matches && invoiceInvoiceNo.contains(searchInvoiceNo);
            }
            
            // Filter by Stock Code (exact match or contains)
            if (stockCode != null && !stockCode.trim().isEmpty()) {
                String searchStockCode = stockCode.trim().toUpperCase();
                String invoiceStockCode = invoice.getStockCode() != null ? invoice.getStockCode().toUpperCase() : "";
                matches = matches && invoiceStockCode.contains(searchStockCode);
            }
            
            // Filter by Description (contains - case insensitive)
            if (description != null && !description.trim().isEmpty()) {
                String searchDesc = description.trim().toUpperCase();
                String invoiceDesc = invoice.getDescription() != null ? invoice.getDescription().toUpperCase() : "";
                matches = matches && invoiceDesc.contains(searchDesc);
            }
            
            // Filter by Customer ID (exact match or contains)
            if (customerId != null && !customerId.trim().isEmpty()) {
                String searchCustomerId = customerId.trim();
                String invoiceCustomerId = invoice.getCustomerId() != null ? String.valueOf(invoice.getCustomerId()) : "";
                matches = matches && invoiceCustomerId.contains(searchCustomerId);
            }
            
            // Filter by Country (contains - case insensitive)
            if (country != null && !country.trim().isEmpty()) {
                String searchCountry = country.trim().toUpperCase();
                String invoiceCountry = invoice.getCountry() != null ? invoice.getCountry().toUpperCase() : "";
                matches = matches && invoiceCountry.contains(searchCountry);
            }
            
            if (matches) {
                filteredInvoices.add(invoice);
            }
        }
        
        // Implement pagination on filtered results
        int totalElements = filteredInvoices.size();
        int startIndex = page * size;
        int endIndex = Math.min(startIndex + size, totalElements);
        
        List<Invoice> pageContent = (startIndex < totalElements) 
            ? new ArrayList<>(filteredInvoices.subList(startIndex, endIndex))
            : new ArrayList<>();
        
        Pageable pageable = PageRequest.of(page, size);
        Page<Invoice> invoicePage = new PageImpl<>(pageContent, pageable, totalElements);
        
        System.out.println("✅ Found " + totalElements + " matching invoices, showing page " + (page + 1));
        
        return invoicePage;
    }
}

