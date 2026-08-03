import { defineGkdApp } from '@gkd-kit/define';

export default defineGkdApp({
  id: 'tv.danmaku.bili',
  name: '哔哩哔哩',
  groups: [
    {
      key: 1,
      name: '开屏广告',
      activityIds: ['tv.danmaku.bili.MainActivityV2'],
      rules: [
        {
          key: 1,
          matches: '[vid="count_down"][visibleToUser=true][clickable=true]',
        },
      ],
    },
  ],
});
