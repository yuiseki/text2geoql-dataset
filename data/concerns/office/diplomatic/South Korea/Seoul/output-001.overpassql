[out:json][timeout:30000];
area["name:en"="South Korea"]->.outer;
area["name:en"="Seoul"]->.inner;
(
  nwr["office"="diplomatic"](area.inner)(area.outer);
);
out geom;
