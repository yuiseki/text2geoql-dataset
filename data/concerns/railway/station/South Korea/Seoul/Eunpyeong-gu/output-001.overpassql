[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Eunpyeong-gu"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
