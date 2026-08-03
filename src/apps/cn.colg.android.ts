import { defineGkdApp } from '@gkd-kit/define';

export default defineGkdApp({
  id: 'cn.colg.android',
  name: 'COLG玩家社区',
  groups: [
    {
      key: 1,
      name: '开屏广告',
      activityIds: ['.compose.ui.ad.ADActivity'],
      rules: [
        {
          key: 1,
          name: '点击跳过',
          matches: '@[clickable=true] > [text$=" 跳过"]',
        },
      ],
    },
  ],
});
