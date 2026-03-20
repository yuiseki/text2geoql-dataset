[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Nishiyodogawa Ward"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
