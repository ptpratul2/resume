#!/bin/bash

# API Connection Test Script
# Tests all endpoints used by the Resume App

API_BASE="http://localhost:8000"
TOKEN="token 19381cf6f577ae0:b2ca674abcc0259"

echo "🔍 Testing Resume App API Connections..."
echo "========================================="
echo ""

# Test 1: Designations
echo "1️⃣  Testing Designations API..."
RESPONSE=$(curl -s -H "Authorization: $TOKEN" "${API_BASE}/api/resource/Designation?fields=%5B%22name%22%5D&limit_page_length=3")
if echo "$RESPONSE" | grep -q "data"; then
    echo "✅ Designations: OK"
    echo "   Sample: $(echo $RESPONSE | head -c 100)..."
else
    echo "❌ Designations: FAILED"
    echo "   Response: $RESPONSE"
fi
echo ""

# Test 2: Companies
echo "2️⃣  Testing Companies API..."
RESPONSE=$(curl -s -H "Authorization: $TOKEN" "${API_BASE}/api/resource/Company?fields=%5B%22name%22%5D&limit_page_length=3")
if echo "$RESPONSE" | grep -q "data"; then
    echo "✅ Companies: OK"
else
    echo "❌ Companies: FAILED"
fi
echo ""

# Test 3: Departments
echo "3️⃣  Testing Departments API..."
RESPONSE=$(curl -s -H "Authorization: $TOKEN" "${API_BASE}/api/resource/Department?fields=%5B%22name%22%5D&limit_page_length=3")
if echo "$RESPONSE" | grep -q "data"; then
    echo "✅ Departments: OK"
else
    echo "❌ Departments: FAILED"
fi
echo ""

# Test 4: Employment Types
echo "4️⃣  Testing Employment Types API..."
RESPONSE=$(curl -s -H "Authorization: $TOKEN" "${API_BASE}/api/resource/Employment%20Type?fields=%5B%22name%22%5D&limit_page_length=3")
if echo "$RESPONSE" | grep -q "data"; then
    echo "✅ Employment Types: OK"
else
    echo "❌ Employment Types: FAILED"
fi
echo ""

# Test 5: Locations
echo "5️⃣  Testing Locations API..."
RESPONSE=$(curl -s -H "Authorization: $TOKEN" "${API_BASE}/api/resource/Location?fields=%5B%22name%22%5D&limit_page_length=3")
if echo "$RESPONSE" | grep -q "data"; then
    echo "✅ Locations: OK"
else
    echo "❌ Locations: FAILED"
fi
echo ""

# Test 6: Job Openings
echo "6️⃣  Testing Job Openings API..."
RESPONSE=$(curl -s -H "Authorization: $TOKEN" "${API_BASE}/api/resource/Job%20Opening?fields=%5B%22name%22%2C%22job_title%22%5D&limit_page_length=3")
if echo "$RESPONSE" | grep -q "data"; then
    echo "✅ Job Openings: OK"
    COUNT=$(echo "$RESPONSE" | grep -o '"name"' | wc -l)
    echo "   Found $COUNT job opening(s)"
else
    echo "❌ Job Openings: FAILED"
fi
echo ""

# Test 7: Job Applicants
echo "7️⃣  Testing Job Applicants API..."
RESPONSE=$(curl -s -H "Authorization: $TOKEN" "${API_BASE}/api/resource/Job%20Applicant?fields=%5B%22name%22%2C%22applicant_name%22%5D&limit_page_length=3")
if echo "$RESPONSE" | grep -q "data"; then
    echo "✅ Job Applicants: OK"
    COUNT=$(echo "$RESPONSE" | grep -o '"name"' | wc -l)
    echo "   Found $COUNT applicant(s)"
else
    echo "❌ Job Applicants: FAILED"
fi
echo ""

# Test 8: Users (for interviewers)
echo "8️⃣  Testing Users API..."
RESPONSE=$(curl -s -H "Authorization: $TOKEN" "${API_BASE}/api/resource/User?fields=%5B%22name%22%2C%22full_name%22%5D&limit_page_length=3")
if echo "$RESPONSE" | grep -q "data"; then
    echo "✅ Users: OK"
else
    echo "❌ Users: FAILED"
fi
echo ""

# Test 9: Interview Rounds
echo "9️⃣  Testing Interview Rounds API..."
RESPONSE=$(curl -s -H "Authorization: $TOKEN" "${API_BASE}/api/resource/Interview%20Round?fields=%5B%22name%22%2C%22round_name%22%5D&limit_page_length=3")
if echo "$RESPONSE" | grep -q "data"; then
    echo "✅ Interview Rounds: OK"
else
    echo "❌ Interview Rounds: FAILED"
fi
echo ""

# Test 10: Interviews
echo "🔟 Testing Interviews API..."
RESPONSE=$(curl -s -H "Authorization: $TOKEN" "${API_BASE}/api/resource/Interview?fields=%5B%22name%22%5D&limit_page_length=3")
if echo "$RESPONSE" | grep -q "data"; then
    echo "✅ Interviews: OK"
else
    echo "❌ Interviews: FAILED"
fi
echo ""

echo "========================================="
echo "✅ API Connection Tests Complete!"
echo ""
echo "📱 Frontend URL: http://localhost:3000"
echo "🔌 Backend URL: $API_BASE"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Go to 'Create Job Opening' to test dropdown data"
echo "3. Try creating a job opening"
echo "4. Upload resumes for the job"

