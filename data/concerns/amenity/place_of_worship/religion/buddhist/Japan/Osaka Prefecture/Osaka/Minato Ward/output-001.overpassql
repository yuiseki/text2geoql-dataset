[out:json][timeout:30];
area["name:en"="Osaka Prefecture"]->.outer;
area["name:en"="Minato Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="buddhist"](area.inner)(area.outer);
);
out geom;
