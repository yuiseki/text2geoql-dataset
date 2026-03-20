[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Jungnang-gu"]->.inner;
(
  nwr["tourism"="gallery"](area.inner)(area.outer);
);
out geom;
