# 📦 Publishing Code Sage to PyPI

This guide walks you through publishing Code Sage to the Python Package Index (PyPI).

## ✅ Prerequisites Checklist

Your package is ready! You have:
- ✅ `setup.py` with package metadata
- ✅ `pyproject.toml` with build configuration
- ✅ `README.md` for package description
- ✅ `LICENSE` file (MIT)
- ✅ All source code in `code_sage/` directory
- ✅ Tests in `tests/` directory
- ✅ Clean git repository

---

## 🚀 Publishing Steps

### Step 1: Install Publishing Tools

```bash
pip install --upgrade pip setuptools wheel twine build
```

### Step 2: Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create your account
3. Verify your email

### Step 3: Create API Token

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Set scope to "Entire account" (or specific project later)
4. **Save the token securely** - you'll only see it once!

### Step 4: Configure PyPI Credentials

Create `~/.pypirc` file:

```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE
EOF

chmod 600 ~/.pypirc
```

Replace `pypi-YOUR-API-TOKEN-HERE` with your actual token.

### Step 5: Clean Previous Builds

```bash
cd /Users/suhai/Code-Sage
rm -rf build/ dist/ *.egg-info
```

### Step 6: Build the Package

```bash
python -m build
```

This creates:
- `dist/code-sage-1.0.0.tar.gz` (source distribution)
- `dist/code_sage-1.0.0-py3-none-any.whl` (wheel distribution)

### Step 7: Check the Package

```bash
twine check dist/*
```

This validates your package before uploading.

### Step 8: Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ code-sage
```

### Step 9: Upload to PyPI (Production)

```bash
twine upload dist/*
```

### Step 10: Verify Installation

```bash
pip install code-sage
code-sage --version
```

---

## 🎯 Quick Command Summary

```bash
# 1. Install tools
pip install --upgrade pip setuptools wheel twine build

# 2. Clean and build
cd /Users/suhai/Code-Sage
rm -rf build/ dist/ *.egg-info
python -m build

# 3. Check package
twine check dist/*

# 4. Upload (you'll be prompted for credentials)
twine upload dist/*
```

---

## 📝 Important Notes

### Package Name
- Your package is named `code-sage`
- Users will install with: `pip install code-sage`
- Check availability at: https://pypi.org/project/code-sage/

### Version Management
- Current version: `1.0.0` (in `setup.py` and `pyproject.toml`)
- For updates, increment version number
- Follow semantic versioning (MAJOR.MINOR.PATCH)

### Future Updates

To release version 1.0.1, 1.1.0, etc:

```bash
# 1. Update version in setup.py and pyproject.toml and __init__.py
# 2. Commit changes
git add setup.py pyproject.toml code_sage/__init__.py
git commit -m "chore: bump version to 1.0.1"
git tag v1.0.1
git push origin main --tags

# 3. Build and upload
rm -rf build/ dist/ *.egg-info
python -m build
twine check dist/*
twine upload dist/*
```

---

## 🔒 Security Best Practices

1. **Never commit** `.pypirc` to git
2. **Use API tokens** instead of passwords
3. **Rotate tokens** periodically
4. **Test on TestPyPI** before production
5. **Review package contents** before uploading

---

## 🐛 Troubleshooting

### "Package already exists"
- The name might be taken
- Try: `code-sage-ai`, `codesage`, or `code-sage-analyzer`
- Check: https://pypi.org/search/?q=code-sage

### "Invalid distribution"
```bash
# Rebuild from scratch
rm -rf build/ dist/ *.egg-info
python -m build
```

### "403 Forbidden"
- Check your API token is correct
- Verify token hasn't expired
- Ensure token has upload permissions

### "README rendering issues"
```bash
# Test README rendering
pip install readme-renderer
python -m readme_renderer README.md
```

---

## 📊 After Publishing

### Monitor Your Package

1. **PyPI Page**: https://pypi.org/project/code-sage/
2. **Download Stats**: https://pypistats.org/packages/code-sage
3. **Set up badges** in README:

```markdown
[![PyPI version](https://badge.fury.io/py/code-sage.svg)](https://badge.fury.io/py/code-sage)
[![Downloads](https://pepy.tech/badge/code-sage)](https://pepy.tech/project/code-sage)
```

### Announce Your Package

- Twitter/X
- Reddit: r/Python, r/programming
- Hacker News
- Dev.to
- LinkedIn
- Python Weekly newsletter

---

## 🎉 Success!

Once published, users can install with:

```bash
pip install code-sage
```

And use it:

```bash
code-sage analyze myproject/
```

**Your package will be available to millions of Python developers worldwide!** 🌍

---

## 📞 Need Help?

- PyPI Help: https://pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- Issues: Open an issue on your GitHub repo

Good luck with your launch! 🚀
