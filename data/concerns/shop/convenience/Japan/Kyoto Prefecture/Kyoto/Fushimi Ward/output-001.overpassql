[out:json][timeout:30000];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Fushimi Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
