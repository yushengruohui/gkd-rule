import { defineGkdApp } from '@gkd-kit/define';

export default defineGkdApp({
  id: 'com.dragon.read',
  name: '番茄免费小说',
  groups: [
    {
      key: 1,
      name: '更新提示',
      enable: false,
      activityIds: ['com.dragon.read.pages.main.MainFragmentActivity'],
      rules: [
        {
          key: 1,
          matches:
            '@[vid="jzg"][text="以后再说"][clickable=true][visibleToUser=true]',
        },
      ],
    },
  ],
});
