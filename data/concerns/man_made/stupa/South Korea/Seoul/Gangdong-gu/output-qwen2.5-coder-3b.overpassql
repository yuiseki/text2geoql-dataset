[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangdong-gu"]->.inner;
(
  nwr["religion"="buddhist"](area.inner)(area.outer);
);
out geom;
