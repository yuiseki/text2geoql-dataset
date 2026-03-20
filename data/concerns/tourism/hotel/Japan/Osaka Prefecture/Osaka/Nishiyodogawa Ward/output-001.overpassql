[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Nishiyodogawa Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
