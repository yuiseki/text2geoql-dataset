[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Koganei"]->.inner;
(
  nwr["tourism"="gallery"](area.inner)(area.outer);
);
out geom;
