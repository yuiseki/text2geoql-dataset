[out:json][timeout:30000];
area["name:en"="Seoul"]->.outer;
area["name:en"="Dongdaemun-gu"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
