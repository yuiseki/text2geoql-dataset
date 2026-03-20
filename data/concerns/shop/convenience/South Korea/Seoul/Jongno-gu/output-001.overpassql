[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Jongno-gu"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
