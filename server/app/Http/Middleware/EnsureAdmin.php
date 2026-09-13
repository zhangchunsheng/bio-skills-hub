<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class EnsureAdmin
{
    public function handle(Request $request, Closure $next)
    {
        if (!$request->user()?->isAdmin()) {
            return response()->json(['error' => '需要管理员权限'], 403);
        }

        return $next($request);
    }
}
