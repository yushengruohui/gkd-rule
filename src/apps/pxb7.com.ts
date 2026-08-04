import { defineGkdApp } from '@gkd-kit/define';

export default defineGkdApp({
  id: 'pxb7.com',
  name: '螃蟹账号',
  groups: [
    {
      key: 1,
      name: '开屏广告',
      activityIds: ['com.pxb7.entrance.ui.flash.EntranceFlashActivity'],
      rules: [
        {
          key: 1,
          matches: '[vid="tvCountDown"][visibleToUser=true][clickable=true]',
        },
      ],
    },
    {
      key: 2,
      name: '更新提示',
      enable: true,
      activityIds: ['com.pxb7.entrance.ui.main.EntranceMainActivity'],
      rules: [
        {
          key: 1,
          matches:
            '@[vid="ivClose"][clickable=true][visibleToUser=true][parent.getChild(3).vid="tvVersion"][parent.getChild(3).visibleToUser=true]',
        },
      ],
    },
  ],
});
