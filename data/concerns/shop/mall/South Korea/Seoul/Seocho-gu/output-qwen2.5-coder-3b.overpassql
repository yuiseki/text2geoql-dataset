[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Seocho-gu"]->.inner;
(
  nwr["shop"~"mall"](area.inner)(area.outer);
);
out geom;
