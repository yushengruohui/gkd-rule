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
    {
      key: 2,
      name: '视频广告',
      enable: true,
      activityIds: [
        'com.bilibili.ship.theseus.detail.UnitedBizDetailsActivity',
      ],
      rules: [
        {
          key: 1,
          matches:
            '@[vid="more_layout"][clickable=true][visibleToUser=true][parent.parent.vid="ad_tint_frame"]',
        },
        {
          key: 2,
          preKeys: [1],
          matches:
            '@[vid="reason1_layout"][clickable=true][visibleToUser=true] > [text="不想看该内容"][visibleToUser=true]',
        },
      ],
    },
  ],
});
