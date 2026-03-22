[out:json][timeout:30];
area["name:en"="Pomeranian Voivodeship"]->.outer;
area["name:en"="Gdańsk"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;