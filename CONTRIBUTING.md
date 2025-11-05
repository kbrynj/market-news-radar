# Git Commit Guidelines for Market News Radar

## Commit Message Format
```
<type>: <short description>

<optional detailed description>
<optional list of changes>
```

## Commit Types
- **feat**: New feature or enhancement
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependencies

## Natural Commit Points

### During Development
- ✅ After completing a major feature (e.g., "feat: add RSS feed management")
- ✅ After fixing a bug (e.g., "fix: resolve WebSocket connection issues")
- ✅ After adding documentation (e.g., "docs: add API endpoint examples")
- ✅ Before switching to a new feature
- ✅ After UI improvements (e.g., "feat: improve article card layout")

### When to Commit
1. **Feature Complete**: When a user-facing feature works end-to-end
2. **Bug Fixed**: After testing that the fix actually works
3. **Refactoring Done**: After cleaning up code without breaking functionality
4. **Before Experiments**: Save working state before trying risky changes
5. **End of Session**: Before closing for the day
6. **After Testing**: When local tests pass

### Examples for This Project

```bash
# Adding new features
feat: add WebSocket live updates
feat: implement infinite scroll pagination
feat: add sentiment analysis badges

# Improving existing features  
feat: enhance ticker detection with company name matching
feat: improve search with debouncing

# Bug fixes
fix: resolve duplicate article insertion
fix: correct sentiment score calculation
fix: handle missing RSS feed gracefully

# UI/UX improvements
style: improve dark theme contrast
feat: add info modal for scoring explanation
style: make ticker badges more prominent

# Configuration & setup
chore: add Docker configuration
chore: update dependencies to latest versions
docs: add deployment instructions

# Backend improvements
perf: optimize database queries with indexing
refactor: split scraper logic into modules
feat: add article pruning API endpoint
```

## Suggested Commit Rhythm for This Project

### Small commits (every 30-60 min)
- Single component changes
- CSS tweaks
- Small bug fixes

### Medium commits (every 2-3 hours)
- Complete feature additions
- Multiple related changes
- UI redesigns

### Large commits (daily/milestone)
- Major feature completions
- Release preparation
- Architecture changes

## Current Project Areas to Watch

1. **Scraper improvements** - commit after each enhancement
2. **UI/UX changes** - commit when visually complete
3. **API additions** - commit per endpoint or feature
4. **Bug fixes** - commit immediately after verification
5. **Documentation** - commit with related feature or separately

## Quick Commit Commands

```bash
# Stage all changes
git add .

# Check what's staged
git status

# Commit with message
git commit -m "feat: your message here"

# Or commit with detailed message
git commit
# (Opens editor for multi-line message)

# Push to GitHub
git push

# View recent commits
git log --oneline -5
```

## Reminders
- ⚠️ Don't commit broken code
- ✅ Test before committing
- 📝 Write clear commit messages
- 🔄 Push regularly (at least daily)
- 🧪 Run the app after pulling changes
