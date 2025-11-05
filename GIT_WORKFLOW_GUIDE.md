# 🔧 GIT WORKFLOW GUIDE - DSS v2 Project

## 📊 Current Status
- **Repository:** dss-v2
- **Owner:** zeronista
- **Current Branch:** main
- **Remote:** https://github.com/zeronista/dss-v2.git

---

## 🚀 QUICK START - Cơ Bản

### 1️⃣ Kiểm Tra Trạng Thái
```bash
# Xem branch hiện tại và file đã thay đổi
git status

# Xem lịch sử commit
git log --oneline -10

# Xem các branch
git branch -a
```

### 2️⃣ Commit & Push Thay Đổi
```bash
# Bước 1: Thêm file vào staging
git add .                          # Thêm TẤT CẢ files
git add file1.py file2.md          # Thêm files cụ thể
git add python-apis/               # Thêm cả folder

# Bước 2: Commit với message
git commit -m "feat: Add full data mode to Sales Manager API"

# Bước 3: Push lên GitHub
git push origin main
```

### 3️⃣ Pull Thay Đổi Mới Từ GitHub
```bash
# Lấy code mới nhất từ remote
git pull origin main

# Hoặc fetch + merge (an toàn hơn)
git fetch origin
git merge origin/main
```

---

## 🌿 BRANCHING STRATEGY

### Tạo Branch Mới (Recommended)
```bash
# Tạo branch cho feature mới
git checkout -b feature/full-data-mode
git checkout -b fix/stockcode-10002-error
git checkout -b docs/update-readme

# Hoặc tách 2 lệnh
git branch feature/async-api
git checkout feature/async-api

# Làm việc trên branch...
git add .
git commit -m "feat: Implement async processing"

# Push branch lên GitHub
git push origin feature/full-data-mode
```

### Merge Branch
```bash
# Quay về main
git checkout main

# Pull code mới nhất
git pull origin main

# Merge branch feature vào main
git merge feature/full-data-mode

# Push main đã merge
git push origin main

# Xóa branch cũ (optional)
git branch -d feature/full-data-mode
git push origin --delete feature/full-data-mode
```

---

## 📝 COMMIT MESSAGE CONVENTION

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: Tính năng mới
- **fix**: Sửa lỗi
- **docs**: Thay đổi documentation
- **style**: Format code (không ảnh hưởng logic)
- **refactor**: Refactor code
- **perf**: Cải thiện performance
- **test**: Thêm/sửa tests
- **chore**: Công việc maintenance (build, dependencies...)

### Ví Dụ
```bash
# Feature mới
git commit -m "feat(sales-api): Add full data loading (530K transactions)"

# Sửa lỗi
git commit -m "fix(sales-api): StockCode 10002 not found error"

# Documentation
git commit -m "docs: Add FULL_DATA_UPGRADE_SUMMARY.md"

# Performance
git commit -m "perf(sales-api): Optimize Apriori with 100 products + 20K window"

# Với body chi tiết
git commit -m "feat(sales-api): Load full dataset instead of 50K subset

- Remove head(50000) limitation
- Load 530,104 transactions from CSV
- Update Apriori params: 100 products, 20K window
- Add detailed logging for data stats

Fixes #123"
```

---

## 🔄 COMMON WORKFLOWS

### Workflow 1: Làm Việc Trên Main (Simple)
```bash
# 1. Pull code mới nhất
git pull origin main

# 2. Làm việc & thay đổi code...

# 3. Kiểm tra thay đổi
git status
git diff                    # Xem chi tiết thay đổi

# 4. Commit
git add .
git commit -m "feat: Add new feature"

# 5. Push
git push origin main
```

### Workflow 2: Làm Việc Trên Feature Branch (Recommended)
```bash
# 1. Tạo branch mới từ main
git checkout main
git pull origin main
git checkout -b feature/my-feature

# 2. Làm việc & commit
git add .
git commit -m "feat: Implement my feature"

# 3. Push feature branch
git push origin feature/my-feature

# 4. Tạo Pull Request trên GitHub
# (Làm trên GitHub UI)

# 5. Sau khi merge, quay về main
git checkout main
git pull origin main
git branch -d feature/my-feature
```

### Workflow 3: Sửa Lỗi Nhanh (Hotfix)
```bash
# 1. Tạo hotfix branch từ main
git checkout main
git checkout -b hotfix/critical-bug

# 2. Sửa lỗi
git add .
git commit -m "fix: Critical bug in sales API"

# 3. Merge ngay vào main
git checkout main
git merge hotfix/critical-bug
git push origin main

# 4. Xóa hotfix branch
git branch -d hotfix/critical-bug
```

---

## 🔍 USEFUL COMMANDS

### Xem Thay Đổi
```bash
# Xem files đã thay đổi
git status

# Xem chi tiết thay đổi (chưa staged)
git diff

# Xem chi tiết thay đổi (đã staged)
git diff --staged

# Xem thay đổi của 1 file cụ thể
git diff python-apis/sales_manager_api.py

# Xem lịch sử của 1 file
git log --follow python-apis/sales_manager_api.py
```

### Hoàn Tác Thay Đổi
```bash
# Hủy thay đổi 1 file (NGUY HIỂM!)
git checkout -- filename.py

# Hủy tất cả thay đổi (NGUY HIỂM!)
git reset --hard HEAD

# Xóa file khỏi staging (giữ thay đổi)
git reset HEAD filename.py

# Hoàn tác commit gần nhất (giữ thay đổi)
git reset --soft HEAD~1

# Hoàn tác commit gần nhất (XÓA thay đổi)
git reset --hard HEAD~1

# Tạo commit mới hoàn tác commit cũ (AN TOÀN)
git revert <commit-hash>
```

### Stash (Cất Thay Đổi Tạm Thời)
```bash
# Cất thay đổi hiện tại
git stash save "Work in progress on feature X"

# Xem danh sách stash
git stash list

# Lấy lại thay đổi gần nhất
git stash pop

# Lấy lại stash cụ thể
git stash apply stash@{0}

# Xóa stash
git stash drop stash@{0}
```

### Remote
```bash
# Xem remote repository
git remote -v

# Thêm remote
git remote add origin https://github.com/zeronista/dss-v2.git

# Thay đổi remote URL
git remote set-url origin https://github.com/zeronista/dss-v2.git

# Xóa remote
git remote remove origin
```

---

## 🎯 SPECIFIC TO YOUR PROJECT

### Commit Recent Changes (Full Data Upgrade)
```bash
# Check current changes
git status

# Review changes
git diff python-apis/sales_manager_api.py

# Add all changes
git add .

# Commit with detailed message
git commit -m "feat(sales-api): Upgrade to full data mode (530K transactions)

Changes:
- Remove 50K transaction limit in load_data()
- Load all 530,104 transactions from CSV
- Optimize Apriori: 100 products + 20K window
- Remove check_product_in_full_csv() function
- Simplify error handling
- Add detailed data statistics logging

Fixes: StockCode 10002 not found issue
Performance: +400MB RAM, maintains speed with smart filtering
Documentation: FULL_DATA_UPGRADE_SUMMARY.md"

# Push to GitHub
git push origin main
```

### Create Feature Branch for Async Optimization
```bash
# Create new branch
git checkout -b feature/async-optimization

# Make changes...

# Commit
git add .
git commit -m "feat(sales-api): Add async processing with Gunicorn workers"

# Push
git push origin feature/async-optimization

# Create Pull Request on GitHub
```

### Check What Changed Since Last Commit
```bash
# Files modified
git status

# Detailed changes
git diff

# Compare with last commit
git diff HEAD

# Compare with 2 commits ago
git diff HEAD~2
```

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue 1: Conflict Khi Pull
```bash
# Khi gặp conflict
git pull origin main
# CONFLICT...

# Giải quyết:
# 1. Mở file conflict, sửa thủ công
# 2. Xóa các markers: <<<<<<<, =======, >>>>>>>
# 3. Add và commit
git add .
git commit -m "fix: Resolve merge conflict"
git push origin main
```

### Issue 2: Push Bị Reject
```bash
# Error: Updates were rejected...

# Giải quyết:
git pull origin main --rebase
git push origin main

# Hoặc force push (NGUY HIỂM - chỉ dùng khi chắc chắn)
git push origin main --force
```

### Issue 3: Commit Nhầm File
```bash
# Đã commit nhưng chưa push
git reset --soft HEAD~1    # Hoàn tác commit, giữ changes
git reset HEAD filename    # Xóa file khỏi staging
git commit -m "..."        # Commit lại

# Đã push rồi
git revert <commit-hash>   # Tạo commit mới hoàn tác
git push origin main
```

### Issue 4: Quên Tạo Branch
```bash
# Đã code nhiều trên main, muốn chuyển sang branch
git stash                           # Cất code
git checkout -b feature/my-feature  # Tạo branch mới
git stash pop                       # Lấy code lại
git add .
git commit -m "..."
git push origin feature/my-feature
```

---

## 📚 .gitignore Configuration

```bash
# Current .gitignore should include:
__pycache__/
*.pyc
*.pyo
.DS_Store
.env
*.log
nohup.out
.vscode/
.idea/
venv/
env/
node_modules/
target/
*.class
```

Check your .gitignore:
```bash
cat .gitignore
```

---

## 🎓 BEST PRACTICES

### ✅ DO:
1. **Commit thường xuyên** với messages rõ ràng
2. **Pull trước khi làm việc** mỗi ngày
3. **Tạo branch cho feature lớn**
4. **Review code trước khi commit**
5. **Test trước khi push**
6. **Viết commit message có ý nghĩa**

### ❌ DON'T:
1. **Commit files nhạy cảm** (.env, passwords...)
2. **Force push lên main** (trừ khi thật sự cần)
3. **Commit code lỗi** lên main
4. **Push trực tiếp** không test
5. **Viết commit message kiểu** "update", "fix", "abc"
6. **Commit file binary lớn** (videos, images...)

---

## 🔗 QUICK REFERENCE

```bash
# DAILY WORKFLOW
git pull origin main          # Lấy code mới
# ... work ...
git status                    # Check changes
git add .                     # Stage changes
git commit -m "feat: ..."     # Commit
git push origin main          # Push

# BRANCHING
git checkout -b feature/xxx   # Tạo branch
git checkout main             # Switch branch
git merge feature/xxx         # Merge branch
git branch -d feature/xxx     # Delete branch

# STASH
git stash                     # Cất changes
git stash pop                 # Lấy lại

# UNDO
git reset --soft HEAD~1       # Undo commit (keep changes)
git checkout -- file.py       # Discard file changes

# REMOTE
git remote -v                 # Show remotes
git push origin main          # Push to main
git pull origin main          # Pull from main
```

---

## 📞 HELP

### Git Cheat Sheet
```bash
# Download official Git cheat sheet
wget https://education.github.com/git-cheat-sheet-education.pdf
```

### Git Documentation
- Official Docs: https://git-scm.com/doc
- GitHub Guides: https://guides.github.com/
- Atlassian Git Tutorial: https://www.atlassian.com/git/tutorials

### Interactive Learning
- Learn Git Branching: https://learngitbranching.js.org/
- Git Immersion: https://gitimmersion.com/

---

## 🎯 YOUR NEXT STEPS

1. **Check current status:**
   ```bash
   git status
   git log --oneline -5
   ```

2. **Commit recent changes:**
   ```bash
   git add .
   git commit -m "feat: Full data mode + documentation"
   git push origin main
   ```

3. **Create feature branch for async:**
   ```bash
   git checkout -b feature/async-workers
   # Work on async optimization...
   ```

4. **Verify on GitHub:**
   - Visit: https://github.com/zeronista/dss-v2
   - Check commits, branches, files

---

**Happy Coding! 🚀**
