[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Yodogawa Ward"]->.inner;
(
  nwr["tourism"="gallery"](area.inner)(area.outer);
);
out geom;
