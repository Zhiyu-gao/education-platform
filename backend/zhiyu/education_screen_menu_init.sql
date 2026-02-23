-- 中央控制台新增「可视化大屏」菜单

INSERT INTO sys_menu (
  menu_name, parent_id, order_num, path, component, is_frame, is_cache,
  menu_type, visible, status, perms, icon, create_by, create_time, remark
)
SELECT
  '可视化大屏', 0, 2, 'educationScreen', 'education/screen', 1, 0,
  'C', '0', '0', 'education:screen:view', 'dashboard', 'admin', NOW(), '中央控制台可视化大屏'
WHERE NOT EXISTS (
  SELECT 1 FROM sys_menu WHERE component = 'education/screen'
);

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, m.menu_id
FROM sys_menu m
WHERE m.component = 'education/screen'
  AND NOT EXISTS (
    SELECT 1 FROM sys_role_menu rm WHERE rm.role_id = 1 AND rm.menu_id = m.menu_id
  );

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 2, m.menu_id
FROM sys_menu m
WHERE m.component = 'education/screen'
  AND NOT EXISTS (
    SELECT 1 FROM sys_role_menu rm WHERE rm.role_id = 2 AND rm.menu_id = m.menu_id
  );
