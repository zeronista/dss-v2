package com.group5.dss.repository;

import com.group5.dss.model.Invoice;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface InvoiceRepository extends MongoRepository<Invoice, String> {
    // MongoRepository already provides findAll(Pageable) method
}

