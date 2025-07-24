#!/bin/bash
export NODE_ENV=development
npm run dev 2>&1 | tee dev-server.log