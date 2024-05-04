// Important note: SubArea: Japan/Saitama Prefecture/Saitama
[out:json][timeout:30000];
area["name:en"="Saitama Prefecture"]->.outer;
area["name:en"="Saitama"]->.inner;
(
  relation["boundary"="administrative"]["admin_level"=8](area.inner)(area.outer);
);
out meta;
