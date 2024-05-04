// Important note: SubArea: Japan/Osaka Prefecture/Osaka
[out:json][timeout:30000];
area["name:en"="Osaka Prefecture"]->.outer;
area["name:en"="Osaka"]->.inner;
(
  relation["boundary"="administrative"]["admin_level"=8](area.inner)(area.outer);
);
out meta;
