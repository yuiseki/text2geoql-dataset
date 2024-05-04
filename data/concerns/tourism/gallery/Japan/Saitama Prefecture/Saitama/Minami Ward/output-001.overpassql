[out:json][timeout:30000];
area["name:en"="Saitama"]->.outer;
area["name:en"="Minami Ward"]->.inner;
(
  nwr["tourism"="gallery"](area.inner)(area.outer);
);
out geom;
