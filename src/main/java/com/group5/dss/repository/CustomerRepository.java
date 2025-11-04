package com.group5.dss.repository;

import com.group5.dss.model.Invoice;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CustomerRepository extends MongoRepository<Invoice, String> {
    
    /**
     * Find all distinct customer IDs
     */
    @Query(value = "{}", fields = "{ 'CustomerID': 1 }")
    List<Invoice> findAllCustomerIds();
    
    /**
     * Find all invoices by customer ID
     */
    List<Invoice> findByCustomerId(Integer customerId);
    
    /**
     * Find invoices by customer ID where InvoiceNo does not start with 'C' (not cancelled)
     */
    @Query("{ 'CustomerID': ?0, 'InvoiceNo': { $not: { $regex: '^C' } } }")
    List<Invoice> findValidInvoicesByCustomerId(Integer customerId);
}
