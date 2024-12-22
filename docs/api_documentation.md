
# API Documentation

## Overview
This document describes the API endpoints for the Quant Trading Strategy system.

## Authentication
All API requests require authentication using JWT tokens.

## Endpoints

### User Management
- POST /api/v1/users/register
- POST /api/v1/users/login
- GET /api/v1/users/me

### Trading
- GET /api/v1/trades
- POST /api/v1/trades
- GET /api/v1/trades/{trade_id}

### Strategy
- GET /api/v1/strategies
- POST /api/v1/strategies
- GET /api/v1/strategies/{strategy_id}
