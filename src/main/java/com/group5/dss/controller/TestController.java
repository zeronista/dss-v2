package com.group5.dss.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class TestController {
    
    @GetMapping("/api-test")
    public String apiTestPage() {
        return "api-test";
    }
}
