[out:json][timeout:30000];
area["name:en"="Aichi Prefecture"]->.outer;
area["name:en"="Mizuho Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="buddhist"](area.inner)(area.outer);
);
out geom;
