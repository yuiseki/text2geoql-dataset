[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Seocho-gu"]->.inner;
(
  nwr["historic"="fort"](area.inner)(area.outer);
);
out geom;
