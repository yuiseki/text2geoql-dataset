[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Dongjak-gu"]->.inner;
(
  nwr["shop"~"mall"](area.inner)(area.outer);
);
out geom;
