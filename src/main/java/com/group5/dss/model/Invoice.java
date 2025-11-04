package com.group5.dss.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "DSS")
public class Invoice {
    
    @Id
    private String id;
    
    @Field("InvoiceNo")
    private Long invoiceNo;
    
    @Field("StockCode")
    private String stockCode;
    
    @Field("Description")
    private String description;
    
    @Field("Quantity")
    private Integer quantity;
    
    @Field("InvoiceDate")
    private String invoiceDate;
    
    @Field("UnitPrice")
    private Double unitPrice;
    
    @Field("CustomerID")
    private Integer customerId;
    
    @Field("Country")
    private String country;

    @Field("TotalPrice")
    private Double totalPrice;

    @Field("InvoiceYear")
    private Integer invoiceYear;

    @Field("InvoiceMonth")
    private Integer invoiceMonth;
}
