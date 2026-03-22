[out:json][timeout:30];
area["name:en"="Pomeranian Voivodeship"]->.outer;
area["name:en"="Gdańsk"]->.inner;
(
  nwr["amenity"="restaurant"](area.inner)(area.outer);
);
out geom;