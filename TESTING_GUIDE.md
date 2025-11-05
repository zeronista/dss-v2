# 🧪 HƯỚNG DẪN TEST HỆ THỐNG DYNAMIC

## 📋 **DANH SÁCH STOCKCODES ĐỂ TEST**

### ✅ **StockCodes CÓ RECOMMENDATIONS (Popular Products)**

Các sản phẩm này được mua nhiều → Có cross-sell patterns:

| StockCode | Transactions | Description | Expected Result |
|-----------|--------------|-------------|-----------------|
| `85123A` | 2,313 | WHITE HANGING HEART T-LIGHT HOLDER | ✅ Có recommendations |
| `22423` | 2,203 | REGENCY CAKESTAND 3 TIER | ✅ Có recommendations |
| `85099B` | 2,159 | JUMBO BAG RED RETROSPOT | ✅ Có recommendations |
| `47566` | 1,727 | PARTY BUNTING | ✅ Có recommendations |
| `84879` | 1,502 | ASSORTED COLOUR BIRD ORNAMENT | ✅ Có recommendations |
| `22086` | 1,210 | PAPER CHAIN KIT 50'S CHRISTMAS | ✅ Có recommendations |

### ⚠️ **StockCodes CÓ THỂ KHÔNG CÓ RECOMMENDATIONS**

Các sản phẩm ít giao dịch hoặc mua độc lập:

| StockCode | Status | Expected Result |
|-----------|--------|-----------------|
| `22623` | Tồn tại nhưng ít cross-sell | ⚠️ Không có recommendations |
| `21754` | Tồn tại nhưng mua riêng lẻ | ⚠️ Có thể không có recommendations |

### ❌ **StockCodes KHÔNG TỒN TẠI**

Test error handling:

| StockCode | Expected Result |
|-----------|-----------------|
| `10002` | ❌ 404 Error: Product not found |
| `FAKE123` | ❌ 404 Error: Product not found |
| `99999` | ❌ 404 Error: Product not found |

---

## 🎯 **CÁC BƯỚC TEST**

### **Test 1: StockCode có recommendations**

1. Mở: http://localhost:8080/dashboard/sales
2. Nhập StockCode: `85123A`
3. Click "🔍 Get Recommendations"

**Kết quả mong đợi:**
- ✅ Hiển thị 1-6 recommendation cards
- ✅ Stats cards cập nhật (Recommendations Found, Potential Revenue, Avg Confidence, Avg Lift)
- ✅ Cross-sell Insights xuất hiện
- ✅ Mỗi recommendation có: Rank, Product Code, Description, Confidence, Lift, Support, Impact

**Ví dụ kết quả:**
```
#1 Recommendation
22086 - PAPER CHAIN KIT 50'S CHRISTMAS
Confidence: 30.4%
Lift: 1.60x
Support: 3.41%
Impact: $33
```

---

### **Test 2: StockCode KHÔNG có recommendations**

1. Nhập StockCode: `22623`
2. Click "🔍 Get Recommendations"

**Kết quả mong đợi:**
- ⚠️ Hiển thị thông báo vàng:
  ```
  ⚠️ No Recommendations Available
  Product "22623" (BOX OF VINTAGE JIGSAW BLOCKS) exists but has no strong cross-sell patterns.
  
  This could mean:
  • Product is rarely bought with other items
  • Not enough transaction history
  • Try lowering confidence threshold or try another product
  ```
- ✅ Stats cards = 0
- ✅ Insights vẫn hiển thị (nếu có timing/revenue data)

---

### **Test 3: StockCode KHÔNG tồn tại**

1. Nhập StockCode: `10002`
2. Click "🔍 Get Recommendations"

**Kết quả mong đợi:**
- ❌ Hiển thị thông báo đỏ:
  ```
  ❌ Product Not Found
  StockCode "10002" does not exist in the database.
  
  Try these popular products:
  85123A, 22086, 22752, 84879, 22623, 22622, 21754, 21755
  ```

---

### **Test 4: API không chạy**

1. Stop API: `./stop.sh`
2. Nhập bất kỳ StockCode nào
3. Click "🔍 Get Recommendations"

**Kết quả mong đợi:**
- ❌ Hiển thị:
  ```
  ❌ Failed to Connect to API
  Failed to fetch
  
  Troubleshooting:
  • Make sure Sales API is running on port 8004
  • Check: http://localhost:8004/health
  • Run: bash start.sh to start services
  ```

---

## 🔬 **TEST BẰNG CURL (Advanced)**

### **Test API trực tiếp:**

```bash
# Test 1: StockCode có recommendations
curl -X POST "http://localhost:8004/generate-recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "85123A",
    "confidence_threshold": 0.3,
    "top_n": 6,
    "min_support": 0.01
  }' | jq

# Test 2: StockCode không có recommendations
curl -X POST "http://localhost:8004/generate-recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "22623",
    "confidence_threshold": 0.3,
    "top_n": 6,
    "min_support": 0.01
  }' | jq

# Test 3: StockCode không tồn tại
curl -X POST "http://localhost:8004/generate-recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "10002",
    "confidence_threshold": 0.3,
    "top_n": 6,
    "min_support": 0.01
  }' | jq

# Test 4: Thay đổi threshold (nhiều recommendations hơn)
curl -X POST "http://localhost:8004/generate-recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "85123A",
    "confidence_threshold": 0.1,
    "top_n": 10,
    "min_support": 0.005
  }' | jq
```

---

## 📊 **TEST BROWSER DEVTOOLS**

### **Mở DevTools (F12) → Network Tab:**

1. Nhập StockCode và click "Get Recommendations"
2. Tìm request: `generate-recommendations`
3. Click vào request
4. **Xem Request:**
   ```json
   {
     "stock_code": "85123A",
     "customer_id": null,
     "confidence_threshold": 0.3,
     "top_n": 6,
     "min_support": 0.01
   }
   ```

5. **Xem Response:**
   ```json
   {
     "success": true,
     "source_product": {
       "stock_code": "85123A",
       "description": "CREAM HANGING HEART T-LIGHT HOLDER"
     },
     "recommendations": [...],
     "total_recommendations": 1
   }
   ```

**✅ CHỨNG MINH:** 
- Response khác nhau cho mỗi StockCode
- Data đến từ API, không phải frontend hardcode
- Mỗi lần request tính toán lại

---

## 🎬 **KỊCH BẢN DEMO CHO VIDEO**

### **Phần 1: Giới thiệu (30s)**
> "Hôm nay tôi sẽ chứng minh hệ thống Sales Manager Dashboard là 100% dynamic, 
> tính toán từ 50,000 giao dịch thực tế, không phải hardcode"

### **Phần 2: Test thành công (1 phút)**
1. Mở dashboard
2. Nhập `85123A`
3. Click "Get Recommendations"
4. **Giải thích:**
   - "Hệ thống tìm thấy sản phẩm WHITE HANGING HEART T-LIGHT HOLDER"
   - "Phân tích 50,000 giao dịch bằng Apriori Algorithm"
   - "Tìm thấy 1 recommendation: sản phẩm 22086"
   - "Confidence 30.4% = 30.4% khách mua 85123A cũng mua 22086"
   - "Lift 1.6x = Khả năng mua cùng cao gấp 1.6 lần ngẫu nhiên"

### **Phần 3: Test không có recommendations (1 phút)**
1. Nhập `22623`
2. Click "Get Recommendations"
3. **Giải thích:**
   - "Hệ thống TÌM THẤY sản phẩm BOX OF VINTAGE JIGSAW BLOCKS"
   - "Nhưng KHÔNG CÓ cross-sell patterns đủ mạnh"
   - "Nếu hardcode, sẽ luôn có recommendations!"
   - "Đây là chứng cứ hệ thống tính toán thực tế"

### **Phần 4: Test lỗi (30s)**
1. Nhập `10002`
2. Click "Get Recommendations"
3. **Giải thích:**
   - "Hệ thống báo lỗi: Product Not Found"
   - "Nếu hardcode, sẽ không có lỗi này"
   - "Hệ thống đã TÌM KIẾM trong 50,000 giao dịch và không tìm thấy"

### **Phần 5: Mở DevTools (1 phút)**
1. F12 → Network Tab
2. Nhập `85123A` lại
3. **Show:**
   - Request body: `{"stock_code": "85123A", ...}`
   - Response: Full JSON với recommendations
4. **Giải thích:**
   - "Mỗi lần request, API tính toán lại"
   - "Response khác nhau cho mỗi StockCode"
   - "Không có cache, không có hardcode"

### **Phần 6: Test API trực tiếp (1 phút)**
1. Mở terminal
2. Chạy `curl` command
3. **Show output:**
   - JSON response thực tế
   - Confidence, lift, support values
4. **Giải thích:**
   - "Đây là API backend thực tế"
   - "Tính toán Apriori algorithm"
   - "Kết quả dynamic dựa trên dữ liệu CSV"

### **Phần 7: Kết luận (30s)**
> "Như các bạn đã thấy:
> - Hệ thống tính toán THỰC TẾ từ 50,000 giao dịch
> - Mỗi StockCode cho kết quả KHÁC NHAU
> - Có thể KHÔNG CÓ recommendations nếu data không đủ mạnh
> - Có thể BÁO LỖI nếu product không tồn tại
> - 100% DYNAMIC, 0% hardcode!"

---

## ✅ **CHECKLIST TEST**

- [ ] Test với StockCode phổ biến (85123A) → Có recommendations
- [ ] Test với StockCode ít phổ biến (22623) → Không có recommendations
- [ ] Test với StockCode không tồn tại (10002) → Error 404
- [ ] Mở DevTools → Xem request/response
- [ ] Test với curl → Verify API response
- [ ] Test thay đổi threshold → Kết quả khác nhau
- [ ] Stop API → Verify error message

---

## 🚀 **NEXT STEPS**

Sau khi test xong, bạn có thể:

1. **Thử nghiệm với thresholds khác nhau:**
   - Giảm `confidence_threshold` = 0.1 → Nhiều recommendations hơn
   - Tăng `min_support` = 0.05 → Ít recommendations hơn nhưng chất lượng cao

2. **Test với customer_id:**
   - Nhập Customer ID = `17850`
   - Kết quả sẽ được cá nhân hóa cho khách hàng đó

3. **Xem Top Bundles:**
   - Click "📊 Load Top Bundles"
   - Xem top 10 bundles phổ biến nhất

4. **Kiểm tra log:**
   ```bash
   tail -f python-apis/sales_manager.log
   ```
   - Xem quá trình tính toán thực tế

---

**Chúc bạn test thành công! 🎉**
