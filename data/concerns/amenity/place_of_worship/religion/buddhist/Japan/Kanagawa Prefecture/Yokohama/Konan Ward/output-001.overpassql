[out:json][timeout:30000];
area["name:en"="Kanagawa Prefecture"]->.outer;
area["name:en"="Konan Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="buddhist"](area.inner)(area.outer);
);
out geom;
