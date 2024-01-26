import { useRecoilValue } from 'recoil';

import { Stack, Typography } from '@mui/material';

import { Translator } from 'components/i18n';

import 'assets/logo_dark.svg';
import LogoDark from 'assets/logo_dark.svg?react';
import 'assets/logo_light.svg';
import LogoLight from 'assets/logo_light.svg?react';

import { settingsState } from 'state/settings';

export default function WaterMark() {
  const { theme } = useRecoilValue(settingsState);
  const Logo = theme === 'light' ? LogoLight : LogoDark;
  return (
   <>
   </>
  );
}
