package com.group5.dss.model;

public enum Role {
    ADMIN("Admin/Director"),
    INVENTORY_MANAGER("Inventory Manager"),
    MARKETING_MANAGER("Marketing Manager"),
    SALES_MANAGER("Sales Manager");
    
    private final String displayName;
    
    Role(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
}

