package com.group5.dss.service;

import com.group5.dss.model.Invoice;
import com.group5.dss.repository.InvoiceRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
public class InvoiceService {
    
    @Autowired
    private InvoiceRepository invoiceRepository;
    
    public Page<Invoice> getAllInvoices(int page, int size) {
        // Removed sort to avoid MongoDB memory limit error on large dataset
        // To enable sorting, create an index on the sort field in MongoDB
        Pageable pageable = PageRequest.of(page, size);
        return invoiceRepository.findAll(pageable);
    }
    
    public long getTotalCount() {
        return invoiceRepository.count();
    }
}

