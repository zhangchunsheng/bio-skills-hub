<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    /**
     * 创建默认管理员（可用 ADMIN_EMAIL / ADMIN_PASSWORD 环境变量覆盖）。
     * 首次部署后请立即登录管理后台并修改密码。
     */
    public function run(): void
    {
        $email = env('ADMIN_EMAIL', 'admin@bio-skills.local');
        $password = env('ADMIN_PASSWORD', 'admin123456');

        $admin = User::firstOrNew(['email' => $email]);
        $admin->name = '管理员';
        $admin->password = Hash::needsRehash($admin->password ?? '') || !$admin->exists
            ? $password
            : $admin->password;
        $admin->role = 'admin';
        $admin->save();

        $this->command->info("管理员账号：{$email} / {$password}");
    }
}
