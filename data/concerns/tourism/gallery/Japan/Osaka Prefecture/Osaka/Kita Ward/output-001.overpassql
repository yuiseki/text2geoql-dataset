[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Kita Ward"]->.inner;
(
  nwr["tourism"="gallery"](area.inner)(area.outer);
);
out geom;
